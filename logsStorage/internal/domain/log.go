package domain

import (
	"errors"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type Log struct {
	Timestamp     primitive.Timestamp
	Level					string
	PathName 			string
	Message       string
}

func (l *Log) Validate() error {
	if l.Timestamp.T == 0 {
		return errors.New("timestamp is uninitialized")
	}
	if l.Level == "" {
		return errors.New("level is required")
	}
	if l.PathName == "" {
		return errors.New("pathname is required")
	}
	if l.Message == "" {
		return errors.New("message is required")
	}
	return nil
}