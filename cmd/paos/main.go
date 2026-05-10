package main

import (
	"context"
	"os"

	"personal-agent-os/internal/paos"
)

func main() {
	os.Exit(paos.Main(context.Background(), os.Args[1:], os.Stdout, os.Stderr))
}
