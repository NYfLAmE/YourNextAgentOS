package paos

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

type Document struct {
	Path   string
	Fields map[string]any
	Body   string
}

func ReadDocument(path string) (Document, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return Document{}, err
	}
	raw := string(data)
	if !strings.HasPrefix(raw, "---\n") {
		return Document{Path: path, Fields: map[string]any{}, Body: raw}, nil
	}
	end := strings.Index(raw[4:], "\n---\n")
	if end < 0 {
		return Document{}, fmt.Errorf("frontmatter terminator not found")
	}
	end += 4
	fmText := raw[4:end]
	body := raw[end+5:]
	fields := map[string]any{}
	if strings.TrimSpace(fmText) != "" {
		if err := yaml.Unmarshal([]byte(fmText), &fields); err != nil {
			return Document{}, fmt.Errorf("parse frontmatter: %w", err)
		}
	}
	return Document{Path: path, Fields: normalizeMap(fields), Body: body}, nil
}

func WriteDocument(doc Document) error {
	fm, err := MarshalFrontmatter(doc.Fields)
	if err != nil {
		return err
	}
	body := doc.Body
	if !strings.HasPrefix(body, "\n") {
		body = "\n" + body
	}
	if err := os.MkdirAll(filepath.Dir(doc.Path), 0o755); err != nil {
		return err
	}
	return os.WriteFile(doc.Path, []byte("---\n"+string(fm)+"---"+body), 0o644)
}

func MarshalFrontmatter(fields map[string]any) ([]byte, error) {
	keys := orderedKeys(fields)
	root := &yaml.Node{Kind: yaml.MappingNode}
	for _, key := range keys {
		root.Content = append(root.Content, &yaml.Node{
			Kind:  yaml.ScalarNode,
			Tag:   "!!str",
			Value: key,
		})
		node, err := valueNode(fields[key])
		if err != nil {
			return nil, fmt.Errorf("frontmatter field %s: %w", key, err)
		}
		root.Content = append(root.Content, node)
	}
	var buf bytes.Buffer
	enc := yaml.NewEncoder(&buf)
	enc.SetIndent(2)
	if err := enc.Encode(root); err != nil {
		return nil, err
	}
	if err := enc.Close(); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func valueNode(value any) (*yaml.Node, error) {
	var buf bytes.Buffer
	enc := yaml.NewEncoder(&buf)
	enc.SetIndent(2)
	if err := enc.Encode(value); err != nil {
		return nil, err
	}
	if err := enc.Close(); err != nil {
		return nil, err
	}
	var root yaml.Node
	if err := yaml.Unmarshal(buf.Bytes(), &root); err != nil {
		return nil, err
	}
	if len(root.Content) == 0 {
		return &yaml.Node{Kind: yaml.ScalarNode, Tag: "!!null", Value: ""}, nil
	}
	return root.Content[0], nil
}

func orderedKeys(fields map[string]any) []string {
	priority := []string{
		"artifact_type", "title", "status", "category", "parent_refs",
		"approval_state", "approval_refs", "approved_at", "approved_by",
		"runtime_task_ref", "approval_scope", "risk_level", "source_refs",
		"confidence", "runtime_log_refs", "sent_at", "late_supplement_for",
		"feedback_source", "target_artifact",
	}
	seen := map[string]bool{}
	keys := make([]string, 0, len(fields))
	for _, key := range priority {
		if _, ok := fields[key]; ok {
			keys = append(keys, key)
			seen[key] = true
		}
	}
	var rest []string
	for key := range fields {
		if !seen[key] {
			rest = append(rest, key)
		}
	}
	sort.Strings(rest)
	keys = append(keys, rest...)
	return keys
}

func normalizeMap(in map[string]any) map[string]any {
	out := make(map[string]any, len(in))
	for k, v := range in {
		out[k] = normalizeValue(v)
	}
	return out
}

func normalizeValue(v any) any {
	switch x := v.(type) {
	case map[string]any:
		return normalizeMap(x)
	case map[any]any:
		out := map[string]any{}
		for k, v := range x {
			out[fmt.Sprint(k)] = normalizeValue(v)
		}
		return out
	case []any:
		for i := range x {
			x[i] = normalizeValue(x[i])
		}
		return x
	default:
		return x
	}
}

func fieldString(fields map[string]any, key string) string {
	switch v := fields[key].(type) {
	case string:
		return v
	case nil:
		return ""
	default:
		return fmt.Sprint(v)
	}
}

func fieldStringSlice(fields map[string]any, key string) []string {
	switch v := fields[key].(type) {
	case []string:
		return append([]string(nil), v...)
	case []any:
		out := make([]string, 0, len(v))
		for _, item := range v {
			if item == nil {
				continue
			}
			out = append(out, fmt.Sprint(item))
		}
		return out
	case string:
		if v == "" {
			return nil
		}
		return []string{v}
	default:
		return nil
	}
}

func appendUniqueString(fields map[string]any, key, value string) {
	items := fieldStringSlice(fields, key)
	for _, item := range items {
		if item == value {
			fields[key] = items
			return
		}
	}
	fields[key] = append(items, value)
}
