package repository

import (
	"context"
	"errors"
	"fmt"
	"time"

	mongoApp "github.com/FelishaK/logStorage/internal/app/mongo"
	"github.com/FelishaK/logStorage/internal/domain"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var (
	ErrNoLogsFound = errors.New("no logs found")
	ErrAlreadyExists = errors.New("already exists")
)

type ILogRepository interface {
	GetByLogLevel(ctx context.Context, level string) ([]*domain.Log, error)
	Save(ctx context.Context, data []*domain.Log) error
}

type Storage struct {
	storage *mongoApp.MongoDB
}

func NewStorage(mongoUser string, mongoPassword string, mongoHost string, mongoDB string, mongoPort int, timeout time.Duration) (*Storage, error) {
	const op = "repository.NewStorage"

	store, err := mongoApp.RunMongoDB(mongoUser, mongoPassword, mongoHost, mongoDB, mongoPort, timeout)

	if err != nil {
		return nil, fmt.Errorf("%s: %w", op, err)
	}

	return &Storage{
		storage: store,
	}, nil
}

func (s *Storage) GetByLogLevel(ctx context.Context, level string)  ([]*domain.Log, error) {
	res := []*domain.Log{}
	filter := bson.M{"Level": level}
	cur, err := s.storage.LogsCol.Find(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("error while retrieving data: %s", err.Error())
	}
	if err := cur.All(context.Background(), &res); err != nil {
		return nil, fmt.Errorf("error while retrieving data: %s", err.Error())
	}
	defer cur.Close(ctx)
	if len(res) == 0 {
		return nil, ErrNoLogsFound
	}
	fmt.Printf("DB RES: %+v", res)
	return res, nil
}

func (s *Storage) Save(ctx context.Context, data []*domain.Log) error {
	var logs []interface{}

	for _, v := range data {
		logs = append(logs, v)
	}
	_, err := s.storage.LogsCol.InsertMany(ctx, logs)
	if err != nil {
		if mongo.IsDuplicateKeyError(err) {
			return ErrAlreadyExists
		}
		return fmt.Errorf("error while inserting data: %s", err.Error())
	}
	return nil
}
