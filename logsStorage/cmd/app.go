package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/FelishaK/logStorage/internal/app"
	"github.com/FelishaK/logStorage/internal/app/httpServ"
	"github.com/FelishaK/logStorage/internal/config"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		panic(err)
	}
	log := setupLogger()

	mux := http.NewServeMux()

	app := app.NewApp(log, cfg)
	mux.HandleFunc("/logs/save", app.LogServ.SaveLogs)
	mux.HandleFunc("/logs/get", app.LogServ.GetLogs)

	// creating http server to accept connections
	httpSrv := httpServ.NewHttpServer(cfg.HttpServe.Address, cfg.HttpServe.WriteTimeout, cfg.HttpServe.ReadTimeout, mux)

	go func() {
		httpServ.RunServer(httpSrv)
	}()
	log.Info("Server is running on ",slog.String("address", cfg.HttpServe.Address) )

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT, os.Interrupt)

	<- stop
	err = httpSrv.Shutdown(context.TODO())
	if err != nil {
		panic(err)
	}
	log.Info("Stopping the server . . .")
}	

func setupLogger() *slog.Logger {
	var log *slog.Logger
	opts := slog.HandlerOptions{
		Level: slog.LevelDebug,
	}
	log = slog.New(slog.NewJSONHandler(os.Stdout, &opts))

	return log
}