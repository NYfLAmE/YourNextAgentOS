package paos

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestOpenAICompatibleClientParsesStrictStructuredOutput(t *testing.T) {
	draftBytes, err := json.Marshal(validDraftResponse("."))
	if err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/chat/completions" {
			t.Fatalf("unexpected path: %s", r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-secret" {
			t.Fatalf("unexpected Authorization header")
		}
		var req map[string]any
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Fatal(err)
		}
		if req["model"] != "test-model" {
			t.Fatalf("unexpected model: %#v", req["model"])
		}
		messages := req["messages"].([]any)
		userMsg := messages[1].(map[string]any)["content"].(string)
		if strings.Contains(userMsg, "Private Runtime Log contents are included") {
			t.Fatalf("payload boundary text is wrong: %s", userMsg)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{
			"choices": []map[string]any{
				{"message": map[string]string{"content": string(draftBytes)}},
			},
		})
	}))
	defer server.Close()
	t.Setenv("PAOS_TEST_KEY", "test-secret")
	client := OpenAICompatibleClient{HTTPClient: server.Client()}
	draft, err := client.DraftRuntimeTask(t.Context(), LLMConfig{BaseURL: server.URL + "/v1", Model: "test-model", APIKeyEnv: "PAOS_TEST_KEY"}, LLMPayload{Mode: "parent"})
	if err != nil {
		t.Fatal(err)
	}
	if draft.Title == "" || len(draft.ExecutionSpec.CommandList) != 1 {
		t.Fatalf("unexpected draft: %#v", draft)
	}
}
