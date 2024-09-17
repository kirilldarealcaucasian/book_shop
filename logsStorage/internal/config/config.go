package config

import (
	"fmt"
	"os"
	"time"

	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	HttpServe HttpServer `yaml:"http_server" env-required:"true"` 
	Database Database			`yaml:"database" env-required:"true"`
	RabbitMQ RabbitMQ `yaml:"rabbitmq" env-required:"true"`
}

type HttpServer struct {
	Address string `yaml:"address" env-required:"true"`
	WriteTimeout time.Duration `yaml:"write_timeout" env-default:"4s"`
	ReadTimeout time.Duration `yaml:"read_timeout" env-default:"4s"`
}

type Database struct {
	MongoUser     string `yaml:"mongo_user" env-required:"true"`
	MongoPassword string `yaml:"mongo_password" env-required:"true"`
	MongoHostname string `yaml:"mongo_hostname" env-required:"true"`
	MongoPort  		int `yaml:"mongo_port" env-required:"true"`
	MongoDBName string `yaml:"mongo_db_name" env-required:"true"`
	Timeout time.Duration	`yaml:"timeout" env-required:"true"`
}

type RabbitMQ struct {
	RabbitUser string `yaml:"rabbit_user" env-required:"true"`
	RabbitPassword string `yaml:"rabbit_password" env-required:"true"`
	RabbitHost string	`yaml:"rabbit_host" env-required:"true"`
	RabbitPort int	`yaml:"rabbit_port" env-required:"true"`
}

func LoadConfig() (*Config, error) {
	var cfg Config

	err := FetchConfigByPath(&cfg, os.Getenv("CONFIG_PATH"))
	// err := FetchConfigByPath(&cfg, cfgPath)
	if err != nil {
		return nil, err
	}
	return &cfg, nil
}

func FetchConfigByPath(cfg *Config, path string) error {
	const op = "config.fetchConfigByPath"

	err := cleanenv.ReadConfig(path, cfg)
	if err != nil {
		return fmt.Errorf("%s: %s", op, err.Error())
	}
	return nil
}