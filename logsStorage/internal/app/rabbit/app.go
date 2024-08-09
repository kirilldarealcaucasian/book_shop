package rabbit

import (
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitClient struct {
	con *amqp.Connection
	ch *amqp.Channel
}

func CreateRabbitConnection() (*amqp.Connection, error) {
	// con, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s", os.Getenv("RABBIT_USER"), os.Getenv("RABBIT_PASSWORD"), os.Getenv("RABBIT_HOST")))
	con, err := amqp.Dial("amqp://rmuser:rmpassword@rabbitmq:5672")
	if err != nil {
		return nil, err
	}
	return con, nil
}

func NewRabbitClient(con *amqp.Connection) (*RabbitClient, error) {
	ch, err := con.Channel()
	if err != nil {
		return nil, err
	}
	return &RabbitClient{
		con: con,
		ch: ch,
	}, nil
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
	maxRetrues := 10
	retryDelay := 5 * time.Second
	
	for {
		ch, err := rc.ch.Consume(queue, consumer, autoAck, false, false, false, nil)
		if err != nil {
			log.Println("Faile to consume, attempt:", retries)
			retries++
			if retries <= maxRetrues {
				time.Sleep(retryDelay)
				continue
			} else {
				return ch, err
			}
		}
		return ch, nil
	}
}
