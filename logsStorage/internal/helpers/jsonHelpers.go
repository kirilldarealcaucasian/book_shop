package helpers

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type errorResponse struct {
	Message string `json:"message"`
	StatusCode int `json:"status_code"`
}

func ReadJson(r *http.Request, data any) error {
	d := json.NewDecoder(r.Body)
	err := d.Decode(&data)
	if err != nil {
		return fmt.Errorf("unable to decode json: %s", err.Error())
	}
	return nil
}

func WriteJson(w http.ResponseWriter, status int, data any, headers ...http.Header) error {
	w.WriteHeader(status)
	bytes, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("unable to encode data: %s", err.Error())
	}
	
	w.Header().Add("Content-Type", "application/json")
	_, err = w.Write(bytes)
	if err != nil {
		return fmt.Errorf("error while writing response")
	}
	return nil
}

func WriteError(w http.ResponseWriter, err string, status int) error {
	w.WriteHeader(status)
	errResp := errorResponse{
		Message: err,
		StatusCode: status,
	}
	w.Header().Add("Content-Type", "application/json")
	return WriteJson(w, status, errResp)
}