package mongoApp

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoDB struct {
	Client *mongo.Client
	LogsCol *mongo.Collection
}

func RunMongoDB(mongoUser, mongoPassword, mongoHost, mongoDB string, mongoPort int, timeout time.Duration) (*MongoDB, error) {
	const op = "storage.NewMongoDB"

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	
	conStr := fmt.Sprintf("mongodb://%s:%s@%s:%s", mongoUser, mongoPassword, mongoHost, strconv.Itoa(mongoPort))
	// conStr := "mongodb://user:user@localhost:27017"

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(conStr))
	if err != nil {
		return nil, fmt.Errorf("%s: %w", op, err)
	}

	err = client.Ping(ctx, nil)
       if err != nil {
				log.Printf("%s: %s", op, err.Error())
				return nil, err
       }
	logsCol:= client.Database(mongoDB).Collection("logs")

	log.Println("Successful connection to mongoDB")
	return &MongoDB {
		Client: client,
		LogsCol: logsCol,
	}, nil
}

func (mc *MongoDB) StopMongo(ctx context.Context) error {
	err := mc.Client.Disconnect(ctx)
	if err != nil {
		log.Printf("Failed to stop mongo %s", err.Error())
		return fmt.Errorf("failed to stop mongoD: ")
	}
	return nil
}
