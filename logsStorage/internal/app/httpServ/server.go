package httpServ

import (
	"net/http"
	"time"
)


func NewHttpServer(address string, writeTimeout, readTimeout time.Duration, mux *http.ServeMux) *http.Server{
	return &http.Server{
		Addr:         address,
		WriteTimeout: writeTimeout,
		ReadTimeout:  readTimeout,
		Handler:      mux,
	}
}

func RunServer(srv *http.Server) {
	if err := srv.ListenAndServe(); err != nil {
			panic(err)
		}
}

