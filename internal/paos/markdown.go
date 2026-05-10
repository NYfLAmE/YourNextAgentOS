package paos

import (
	"fmt"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"unicode"

	"gopkg.in/yaml.v3"
)

var headingRE = regexp.MustCompile(`(?m)^##\s+(.+?)\s*$`)

func slugify(s string) string {
	s = strings.ToLower(strings.TrimSpace(s))
	var b strings.Builder
	lastDash := false
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			b.WriteRune(r)
			lastDash = false
			continue
		}
		if !lastDash {
			b.WriteByte('-')
			lastDash = true
		}
	}
	out := strings.Trim(b.String(), "-")
	if out == "" {
		return "task"
	}
	if len(out) > 80 {
		out = strings.Trim(out[:80], "-")
	}
	return out
}

func relativePath(fromDir, target string) string {
	rel, err := filepath.Rel(fromDir, target)
	if err != nil {
		return target
	}
	return filepath.ToSlash(rel)
}

func repoRel(root, target string) string {
	rel, err := filepath.Rel(root, target)
	if err != nil {
		return target
	}
	return filepath.ToSlash(rel)
}

func resolveRef(fromFile, ref string) string {
	if filepath.IsAbs(ref) {
		return filepath.Clean(ref)
	}
	return filepath.Clean(filepath.Join(filepath.Dir(fromFile), filepath.FromSlash(ref)))
}

func featureDir(root, artifactPath string) (string, error) {
	rel, err := filepath.Rel(root, artifactPath)
	if err != nil {
		return "", err
	}
	parts := strings.Split(filepath.ToSlash(rel), "/")
	if len(parts) < 2 || parts[0] != ".scratch" {
		return "", fmt.Errorf("%s is not under .scratch/<feature>", artifactPath)
	}
	return filepath.Join(root, ".scratch", parts[1]), nil
}

func nextNumber(dir string) int {
	matches, _ := filepath.Glob(filepath.Join(dir, "*.md"))
	maxNum := 0
	re := regexp.MustCompile(`^(\d+)`)
	for _, match := range matches {
		base := filepath.Base(match)
		parts := re.FindStringSubmatch(base)
		if len(parts) != 2 {
			continue
		}
		var n int
		_, _ = fmt.Sscanf(parts[1], "%d", &n)
		if n > maxNum {
			maxNum = n
		}
	}
	return maxNum + 1
}

func extractSection(body, heading string) string {
	matches := headingRE.FindAllStringSubmatchIndex(body, -1)
	for i, m := range matches {
		name := strings.TrimSpace(body[m[2]:m[3]])
		if !strings.EqualFold(name, heading) {
			continue
		}
		start := m[1]
		end := len(body)
		if i+1 < len(matches) {
			end = matches[i+1][0]
		}
		return strings.TrimSpace(body[start:end])
	}
	return ""
}

func appendSectionNote(body, heading, note string) string {
	matches := headingRE.FindAllStringSubmatchIndex(body, -1)
	for i, m := range matches {
		name := strings.TrimSpace(body[m[2]:m[3]])
		if !strings.EqualFold(name, heading) {
			continue
		}
		insertAt := len(body)
		if i+1 < len(matches) {
			insertAt = matches[i+1][0]
		}
		before := strings.TrimRight(body[:insertAt], "\n")
		after := body[insertAt:]
		return before + "\n\n" + strings.TrimSpace(note) + "\n" + after
	}
	return strings.TrimRight(body, "\n") + "\n\n## " + heading + "\n\n" + strings.TrimSpace(note) + "\n"
}

func replaceSection(body, heading, content string) string {
	matches := headingRE.FindAllStringSubmatchIndex(body, -1)
	for i, m := range matches {
		name := strings.TrimSpace(body[m[2]:m[3]])
		if !strings.EqualFold(name, heading) {
			continue
		}
		start := m[1]
		end := len(body)
		if i+1 < len(matches) {
			end = matches[i+1][0]
		}
		before := strings.TrimRight(body[:start], "\n")
		after := strings.TrimLeft(body[end:], "\n")
		replacement := strings.TrimSpace(content)
		if after == "" {
			return before + "\n\n" + replacement + "\n"
		}
		return before + "\n\n" + replacement + "\n\n" + after
	}
	return strings.TrimRight(body, "\n") + "\n\n## " + heading + "\n\n" + strings.TrimSpace(content) + "\n"
}

func extractExecutionSpec(body string) (ExecutionSpec, error) {
	return extractExecutionSpecFromSection(body, "Execution Spec")
}

func extractApprovedBoundary(body string) (ExecutionSpec, error) {
	return extractExecutionSpecFromSection(body, "Approved Boundary")
}

func extractExecutionSpecFromSection(body, heading string) (ExecutionSpec, error) {
	section := extractSection(body, heading)
	if section == "" {
		return ExecutionSpec{}, fmt.Errorf("%s section not found", heading)
	}
	start := strings.Index(section, "```yaml")
	if start < 0 {
		start = strings.Index(section, "```yml")
	}
	if start < 0 {
		return ExecutionSpec{}, fmt.Errorf("%s YAML fence not found", heading)
	}
	startLine := strings.Index(section[start:], "\n")
	if startLine < 0 {
		return ExecutionSpec{}, fmt.Errorf("%s YAML fence is incomplete", heading)
	}
	start += startLine + 1
	end := strings.Index(section[start:], "```")
	if end < 0 {
		return ExecutionSpec{}, fmt.Errorf("%s YAML terminator not found", heading)
	}
	yamlText := section[start : start+end]
	var spec ExecutionSpec
	if err := yaml.Unmarshal([]byte(yamlText), &spec); err != nil {
		return ExecutionSpec{}, fmt.Errorf("parse %s: %w", heading, err)
	}
	return spec, nil
}

func renderExecutionSpec(spec ExecutionSpec) (string, error) {
	data, err := yaml.Marshal(spec)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}

func validateExecutionSpec(spec ExecutionSpec) error {
	if strings.TrimSpace(spec.ExecutionWorkspace.Repo) == "" {
		return fmt.Errorf("execution_workspace.repo is required")
	}
	if strings.TrimSpace(spec.ExecutionWorkspace.Mode) == "" {
		return fmt.Errorf("execution_workspace.mode is required")
	}
	if len(spec.CommandList) == 0 {
		return fmt.Errorf("command_list must include at least one command")
	}
	seen := map[string]bool{}
	for i, cmd := range spec.CommandList {
		if strings.TrimSpace(cmd.ID) == "" {
			return fmt.Errorf("command_list[%d].id is required", i)
		}
		if seen[cmd.ID] {
			return fmt.Errorf("duplicate command id %q", cmd.ID)
		}
		seen[cmd.ID] = true
		if strings.TrimSpace(cmd.Command) == "" {
			return fmt.Errorf("command_list[%s].command is required", cmd.ID)
		}
	}
	if strings.TrimSpace(spec.EnvProfile.Mode) == "" {
		return fmt.Errorf("env_profile.mode is required")
	}
	if strings.TrimSpace(spec.PrivateRuntimeLog.Storage) == "" {
		return fmt.Errorf("private_runtime_log.storage is required")
	}
	return nil
}

func sortedMapKeys[T any](m map[string]T) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}
