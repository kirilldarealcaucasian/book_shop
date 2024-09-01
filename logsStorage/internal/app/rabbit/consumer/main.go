package consumer

import (
	"context"
	"encoding/json"
	"log/slog"
	"time"

	"github.com/FelishaK/logStorage/internal/app/rabbit"
	"github.com/FelishaK/logStorage/internal/service"
	"golang.org/x/sync/errgroup"
)

func MustConsume(log *slog.Logger, lrc chan[]*service.LogRequest) {
	const op = "consumer.Consume"
	con, err := rabbit.CreateRabbitConnection()
	if err != nil {
		log.Error("Failed to create connection to rabbitMQ", slog.String(op, err.Error()))
		panic(err)	
	}
	defer con.Close()

	client, err := rabbit.NewRabbitClient(con)
	if err != nil {
		log.Error("Failed to create rabbitMQ client", slog.String(op, err.Error()))
		panic(err)
	}

	mesBus, err := client.Consume("logs_q", "logs-service", true)
	if err != nil {
		log.Error("Failed to consume", slog.String(op, err.Error()))
		panic(err)
	}

	ctx := context.Background()
	var blocking chan struct{}

	ctx, cancel := context.WithTimeout(ctx, 15 * time.Second)
	defer cancel()
	g, _ := errgroup.WithContext(ctx)
	g.SetLimit(10)

	go func() {
		for message := range mesBus {
			msg := message
			g.Go(func() error {	
				var logs []*service.LogRequest
				err := json.Unmarshal(msg.Body, &logs)
				lrc <- logs
				if err != nil {
					log.Error("Failed to unmarshal a message", slog.String(op, err.Error()))
					panic(err)
				}
				return nil
			})
		}
	}()
		log.Info("Consuming, user CTRL + C to exit")
	<-blocking
		log.Info("Stop consuming . . . ")
}