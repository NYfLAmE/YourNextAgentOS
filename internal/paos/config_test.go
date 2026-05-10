package paos

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestLoadConfigAndStatusDoesNotPrintSecret(t *testing.T) {
	dir := t.TempDir()
	configPath := filepath.Join(dir, "config.yaml")
	err := os.WriteFile(configPath, []byte(`
runtime_dir: /tmp/paos-runtime
worktree_root: /tmp/paos-worktrees
llm:
  base_url: http://127.0.0.1:9999/v1
  model: test-model
  api_key_env: PAOS_TEST_API_KEY
`), 0o600)
	if err != nil {
		t.Fatal(err)
	}
	t.Setenv("PAOS_TEST_API_KEY", "secret-value-that-must-not-print")
	cfg, found, err := LoadConfig(configPath)
	if err != nil {
		t.Fatal(err)
	}
	if !found {
		t.Fatal("expected config to be found")
	}
	if cfg.LLM.BaseURL != "http://127.0.0.1:9999/v1" || cfg.LLM.Model != "test-model" || cfg.LLM.APIKeyEnv != "PAOS_TEST_API_KEY" {
		t.Fatalf("unexpected config: %#v", cfg.LLM)
	}
	var out bytes.Buffer
	if err := RunCLI(t.Context(), []string{"--root", dir, "--config", configPath, "status"}, &out, &bytes.Buffer{}, nil); err != nil {
		t.Fatal(err)
	}
	if strings.Contains(out.String(), "secret-value-that-must-not-print") {
		t.Fatalf("status leaked secret value:\n%s", out.String())
	}
}

func TestLoadConfigMissingUsesPrivateDefaults(t *testing.T) {
	cfg, found, err := LoadConfig(filepath.Join(t.TempDir(), "missing.yaml"))
	if err != nil {
		t.Fatal(err)
	}
	if found {
		t.Fatal("expected missing config")
	}
	if cfg.RuntimeDir == "" || cfg.WorktreeRoot == "" {
		t.Fatalf("expected private defaults: %#v", cfg)
	}
}
