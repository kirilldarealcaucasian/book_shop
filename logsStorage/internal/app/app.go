package app

import (
	"log/slog"

	"github.com/FelishaK/logStorage/internal/app/rabbit/consumer"
	"github.com/FelishaK/logStorage/internal/config"
	"github.com/FelishaK/logStorage/internal/handlers"
	"github.com/FelishaK/logStorage/internal/repository"
	"github.com/FelishaK/logStorage/internal/service"
	servicepack "github.com/FelishaK/logStorage/internal/service"
)

type App struct {
	LogServ *handlers.LogServer
}

func NewApp(log *slog.Logger, cfg *config.Config) *App {
	const op = "app.NewApp"

	// initializing a database
	repo, err := repository.NewStorage(cfg.Database.MongoUser, cfg.Database.MongoPassword, cfg.Database.MongoHostname, cfg.Database.MongoDBName, cfg.Database.MongoPort, cfg.Database.Timeout)

	if err != nil {
		log.Error("Error while starting db", slog.String(op, err.Error()))
		panic(err)
	}
	
	service := service.NewLogService(cfg, log, repo)

	logServ := handlers.NewLogServer(log, service)

	// init consume process
	log.Info("Creating logs channel . . .")
	// consumer reads data from the
	logs := make(chan []*servicepack.LogRequest)
	go func(){
		for {
			resLogs := <- logs
			log.Info("Saving logs to the db . . .")
			service.SaveLogs(resLogs)
			continue
		}	
	}()
	consumer.MustConsume(log, logs)

	return &App{
		LogServ: logServ,
	}
}