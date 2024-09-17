package rabbit

import (
	"fmt"
	"log"
	"time"

	"github.com/FelishaK/logStorage/internal/config"
	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitClient struct {
	con *amqp.Connection
	ch *amqp.Channel
}

func CreateRabbitConnection(cfg *config.Config) (*amqp.Connection, error) {
	retries := 0
	maxRetries := 5
	retryDelay := 5 * time.Second

	for {
		con, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s", cfg.RabbitMQ.RabbitUser, cfg.RabbitMQ.RabbitPassword, cfg.RabbitMQ.RabbitHost))
		if err != nil {
			log.Println("failed to connect to RabbitMQ")
			retries++
			if retries <= maxRetries {
				time.Sleep(retryDelay)
				continue
			}
			return nil, err
		}
		return con, nil
	}
}

func NewRabbitClient(con *amqp.Connection) (*RabbitClient, error) {
	retries := 0
	maxRetries := 5
	retryDelay := 8 * time.Second
	for {
		ch, err := con.Channel()
		if err != nil {
			log.Println("failed to create rabbit channel: ", retries)
			retries++
			if retries <= maxRetries {
				time.Sleep(retryDelay)
				continue
			} else {
				return nil, err
			}
		}
		return &RabbitClient{
		con: con,
		ch: ch,
		}, nil
	}
}

func (rc *RabbitClient) Close() error {
	err := rc.ch.Close()
	if err != nil {
		return err
	}
	return nil
}

func (rc *RabbitClient) CreateBinding(qName, binding, exchange string) error {
	return rc.ch.QueueBind(qName, binding, exchange, false, nil)
}

func (rc *RabbitClient) Consume(queue, consumer string, autoAck bool) (<-chan amqp.Delivery, error) {
	retries := 0
	maxRetries := 10
	retryDelay := 15 * time.Second
	
	for {
		ch, err := rc.ch.Consume(queue, consumer, autoAck, false, false, false, nil)
		if err != nil {
			log.Printf("Consume error: %s", err.Error())
			log.Println("rabbit.Consume: Failed to consume, attempt:", retries)
			retries++
			if retries <= maxRetries {
				time.Sleep(retryDelay)
				continue
			} else {
				return nil, err
			}
		}
		return ch, nil
	}
}
