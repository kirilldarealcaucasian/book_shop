package suite

import (
	"context"
	"log/slog"
	"os"
	"testing"
	"time"

	"github.com/FelishaK/logStorage/internal/app"
	"github.com/FelishaK/logStorage/internal/config"
	"github.com/FelishaK/logStorage/internal/handlers"
)

type Suite struct {
	*testing.T
	Cfg        *config.Config
	LogServ *handlers.LogServer
}

func New(t *testing.T) (context.Context, *Suite) {
	t.Helper()
	t.Parallel()

	cfg, err := config.LoadConfig()

	if err != nil {
		panic(err)
	}

	opts := slog.HandlerOptions{
		Level: slog.LevelDebug,
	}
	log := slog.New(slog.NewJSONHandler(os.Stdout, &opts))

	app := app.NewApp(log, cfg)

	ctx, cancelCtx := context.WithTimeout(context.Background(), time.Duration(time.Minute* 10))
	defer cancelCtx()

	return ctx, &Suite{
		T:   t,
		Cfg: cfg,
		LogServ: app.LogServ,
	}
}