package handlers

import (
	"errors"
	"log/slog"
	"net/http"
	"strings"

	"github.com/FelishaK/logStorage/internal/helpers"
	"github.com/FelishaK/logStorage/internal/service"
)

const (
	levelInfo = "INFO"
	levelWarning = "WARNING"
	levelError = "ERROR"
	levelCritical = "CRITICAL"
)

type LogServer struct {
	Log *slog.Logger
	LogService service.ILogService
}

func NewLogServer(log *slog.Logger, logService *service.LogService) *LogServer {
	return &LogServer{
		Log: log,
		LogService: logService,
	}
}

func (ls *LogServer) GetLogs(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.GetLogs"
	ls.Log.Info("Request", slog.String("op", op))

	// get query param
	logLevel := strings.ToUpper(r.URL.Query().Get("level"))
	
	//validate param 
	if logLevel != levelInfo && logLevel != levelError && logLevel != levelCritical && logLevel != levelWarning {
		helpers.WriteError(w, "invalid log level", 400)
		return 
	}
	logs, err := ls.LogService.GetLogs(logLevel)
	if err != nil {
		if errors.Is(err, service.ErrNotFound) {
			helpers.WriteError(w, err.Error(), 404)
			return
		}
		helpers.WriteError(w, "server error", 500)
		return
	}

	helpers.WriteJson(w, 200, logs)
}


func (ls *LogServer) SaveLogs(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.SaveLogs"
	ls.Log.Info("Request", slog.String("op", op))

	logs := []*service.LogRequest{}
	err := helpers.ReadJson(r, &logs)
	if err != nil {
		helpers.WriteError(w, "invalid data format", 400)
		return
	}
	err = ls.LogService.SaveLogs(logs)
	if err != nil {
		if errors.Is(err, service.ErrDuplicate) {
			helpers.WriteError(w, err.Error(), 409)
			return
		} else if errors.Is(err, service.ErrValidation{}) {
			helpers.WriteError(w, err.Error(), 422)
			return 
		}
		helpers.WriteError(w, "Server error", 500)
		return
	}
	helpers.WriteJson(w, 201, map[string]string{"status": "added"})
}
