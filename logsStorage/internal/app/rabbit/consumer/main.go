package consumer

import (
	"context"
	"encoding/json"
	"log/slog"
	"time"

	"github.com/FelishaK/logStorage/internal/app/rabbit"
	"github.com/FelishaK/logStorage/internal/config"
	"github.com/FelishaK/logStorage/internal/service"
	"golang.org/x/sync/errgroup"
)

func MustConsume(log *slog.Logger, lrc chan[]*service.LogRequest, cfg *config.Config) {
	const op = "consumer.Consume"
	con, err := rabbit.CreateRabbitConnection(cfg)
	if err != nil {
		log.Error("Failed to create connection to rabbitMQ", slog.String(op, err.Error()))
		panic(err)
	}
	log.Info("%s %s", op, "Successful connection to RabbitMQ")
	defer con.Close()

	client, err := rabbit.NewRabbitClient(con)
	if err != nil {
		log.Error("Failed to create rabbitMQ client", slog.String(op, err.Error()))
		panic(err)
	}
	log.Info("%s %s", op, "Rabbit channel has been successfully created")

	mesBus, err := client.Consume("logs_q", "logs-service", true)
	if err != nil {
		log.Error("%s: Failed to consume, %w",op, err)
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
				if err != nil {
					log.Error("Failed to unmarshal a message", slog.String(op, err.Error()))
					panic(err)
				}
				lrc <- logs // write to log request channel
				return nil
			})
		}
	}()
		log.Info("Consuming, user CTRL + C to exit")
	<-blocking
		log.Info("Stop consuming . . . ")
}