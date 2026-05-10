package paos

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

func DefaultConfigPath() string {
	home, err := os.UserHomeDir()
	if err != nil || home == "" {
		return filepath.Join(".personal-agent-os", "config.yaml")
	}
	return filepath.Join(home, ".personal-agent-os", "config.yaml")
}

func LoadConfig(path string) (Config, bool, error) {
	if path == "" {
		path = DefaultConfigPath()
	}
	data, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		cfg := Config{}
		applyConfigDefaults(&cfg)
		return cfg, false, nil
	}
	if err != nil {
		return Config{}, false, fmt.Errorf("read config %s: %w", path, err)
	}
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return Config{}, true, fmt.Errorf("parse config %s: %w", path, err)
	}
	applyConfigDefaults(&cfg)
	return cfg, true, nil
}

func applyConfigDefaults(cfg *Config) {
	home, err := os.UserHomeDir()
	if err != nil || home == "" {
		home = "."
	}
	if cfg.RuntimeDir == "" {
		cfg.RuntimeDir = filepath.Join(home, ".personal-agent-os", "runtime")
	}
	if cfg.WorktreeRoot == "" {
		cfg.WorktreeRoot = filepath.Join(cfg.RuntimeDir, "worktrees")
	}
}

func validateLLMConfig(cfg Config) error {
	if cfg.LLM.BaseURL == "" {
		return errors.New("llm.base_url is required")
	}
	if cfg.LLM.Model == "" {
		return errors.New("llm.model is required")
	}
	if cfg.LLM.APIKeyEnv == "" {
		return errors.New("llm.api_key_env is required")
	}
	if _, ok := os.LookupEnv(cfg.LLM.APIKeyEnv); !ok {
		return fmt.Errorf("environment variable %s is not set", cfg.LLM.APIKeyEnv)
	}
	return nil
}
