package service

import (
	"context"
	"errors"
	"log/slog"
	"time"

	"github.com/FelishaK/logStorage/internal/config"
	"github.com/FelishaK/logStorage/internal/domain"
	"github.com/FelishaK/logStorage/internal/repository"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

type ErrValidation struct{
	Message string
}

func (e ErrValidation) Error() string {
	return e.Message
}

var (
	ErrNotFound = errors.New("not found")
	ErrDuplicate = errors.New("duplicate error")
)

type ILogService interface {
	SaveLogs(logs []*LogRequest) error
	GetLogs(level string) ([]*LogsResponse, error)
}

type LogService struct {
	cfg *config.Config
	log *slog.Logger
	repo repository.ILogRepository
}

type LogsResponse struct {
	Timestamp     string
	Level					string
	Pathname 			string
	Message       string
}

type LogRequest struct {
	UnixTime    	uint32 	`json:"unix_time"`
	Level					string	`json:"level"`
	PathName 			string	`json:"pathname"`
	Message       string	`json:"message"`
}

func NewLogService(cfg *config.Config, log *slog.Logger, repo repository.ILogRepository) *LogService {
	return &LogService{
		cfg: cfg,
		log: log,
		repo: repo,
	}
}

func (ls *LogService) SaveLogs(logs []*LogRequest) error {
	const op = "service.SaveLogs"

	ctx, cancel := context.WithTimeout(context.Background(), ls.cfg.Database.Timeout) 
	defer cancel()
	domainLogs := make([]*domain.Log, len(logs))
	
	for i, v := range logs {
		//convert unix time to primitive.Timestamp
		ts := primitive.Timestamp{
			T: v.UnixTime, 
			I: 0,
		}
		//convert to domain model
		dLog := &domain.Log{
			Timestamp: ts,
			Level: v.Level,
			PathName: v.PathName,
			Message: v.Message,
		}
		//validate domain model
		err := dLog.Validate()
		if err != nil {
			return err
		}
		domainLogs[i] = dLog
	}
	err := ls.repo.Save(ctx, domainLogs)
	if err != nil {
		if errors.Is(err, repository.ErrAlreadyExists) {
			ls.log.Warn("validation error:", slog.String(op, err.Error()))
			return ErrValidation{Message: err.Error()}
		}
		ls.log.Error("Error while inserting data", slog.String(op, err.Error()))
		return err
	}
	return nil
}

func (ls *LogService) GetLogs(level string) ([]*LogsResponse, error) {
	const op = "service.GetLogs"

	ctx, cancel := context.WithTimeout(context.Background(), ls.cfg.Database.Timeout) 
	defer cancel()
	logs, err := ls.repo.GetByLogLevel(ctx, level)
	if err != nil {
		if errors.Is(err, repository.ErrNoLogsFound) {
			return nil, ErrNotFound
		}
		ls.log.Error("error while retrieving records from db", slog.String(op, err.Error()))
		return nil, err
	}

	logsResp := make([]*LogsResponse, len(logs))
	
	for i, v := range logs {
		toTime := time.Unix(int64(v.Timestamp.I), int64(v.Timestamp.I) * 1000)
		timeFmt := toTime.Format("2006-01-02 15:04:05")
		logsResp[i] = &LogsResponse{
			// TODO: fix timestamp to primitive.Timestamp
			Timestamp: timeFmt,
			Level: v.Level,
			Pathname: v.PathName,
			Message: v.Message,
		}
	}
	return logsResp, nil
}
