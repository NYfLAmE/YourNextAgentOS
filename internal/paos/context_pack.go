package paos

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf8"
)

const sourceRefMaxBytes = 64 * 1024

var errBinarySourceRef = errors.New("binary or non-UTF-8 source_ref")

func ResolveSourceRefs(parentPath string, refs []string) []ContextPackItem {
	items := make([]ContextPackItem, 0, len(refs))
	for _, ref := range refs {
		ref = strings.TrimSpace(ref)
		if ref == "" {
			continue
		}
		item := ContextPackItem{
			Ref:    ref,
			Path:   sourceRefDisplayPath(parentPath, ref),
			Source: "frontmatter.source_refs",
		}
		if isExternalSourceRef(ref) {
			item.Status = "excluded"
			item.Reason = "unapproved external URL source_ref"
			items = append(items, item)
			continue
		}
		if reason := sensitiveSourceRefReason(item.Path); reason != "" {
			item.Status = "excluded"
			item.Reason = reason
			items = append(items, item)
			continue
		}
		data, info, err := readSourceRefText(item.Path)
		if err != nil {
			item.Status = "excluded"
			item.Reason = err.Error()
			items = append(items, item)
			continue
		}
		item.Status = "included"
		item.Reason = "explicit source_refs entry"
		item.Bytes = int(info.Size())
		if len(data) > sourceRefMaxBytes {
			item.Truncated = true
			data = truncateValidUTF8(data[:sourceRefMaxBytes])
		}
		item.Content = string(data)
		items = append(items, item)
	}
	return items
}

func sourceRefDisplayPath(parentPath, ref string) string {
	if isExternalSourceRef(ref) {
		return ref
	}
	var path string
	if filepath.IsAbs(ref) {
		path = filepath.Clean(ref)
	} else {
		path = filepath.Clean(filepath.Join(filepath.Dir(parentPath), filepath.FromSlash(ref)))
	}
	if abs, err := filepath.Abs(path); err == nil {
		return abs
	}
	return path
}

func isExternalSourceRef(ref string) bool {
	lower := strings.ToLower(strings.TrimSpace(ref))
	return strings.HasPrefix(lower, "http://") || strings.HasPrefix(lower, "https://")
}

func sensitiveSourceRefReason(path string) string {
	path = filepath.Clean(path)
	if path == filepath.Clean(DefaultConfigPath()) {
		return "sensitive source_ref: paos private config"
	}
	cfg := Config{}
	applyConfigDefaults(&cfg)
	if isWithinPath(path, cfg.RuntimeDir) {
		return "sensitive source_ref: private runtime log"
	}
	for _, part := range strings.Split(filepath.ToSlash(path), "/") {
		if part == ".git" {
			return "sensitive source_ref: git internals"
		}
	}
	base := strings.ToLower(filepath.Base(path))
	ext := strings.ToLower(filepath.Ext(base))
	if base == ".env" || strings.HasPrefix(base, ".env.") || ext == ".pem" || ext == ".key" ||
		strings.Contains(base, "token") || strings.Contains(base, "secret") ||
		strings.Contains(base, "password") || strings.Contains(base, "credential") {
		return "sensitive source_ref: credential-like file"
	}
	return ""
}

func isWithinPath(path, root string) bool {
	path = filepath.Clean(path)
	root = filepath.Clean(root)
	rel, err := filepath.Rel(root, path)
	if err != nil {
		return false
	}
	return rel == "." || (rel != ".." && !strings.HasPrefix(rel, ".."+string(filepath.Separator)))
}

func readSourceRefText(path string) ([]byte, os.FileInfo, error) {
	info, err := os.Stat(path)
	if err != nil {
		return nil, nil, err
	}
	if info.IsDir() {
		return nil, nil, os.ErrInvalid
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, nil, err
	}
	if !isTextData(data) {
		return nil, nil, errBinarySourceRef
	}
	return data, info, nil
}

func isTextData(data []byte) bool {
	if !utf8.Valid(data) {
		return false
	}
	return !strings.Contains(string(data), "\x00")
}

func truncateValidUTF8(data []byte) []byte {
	for len(data) > 0 && !utf8.Valid(data) {
		data = data[:len(data)-1]
	}
	return data
}
