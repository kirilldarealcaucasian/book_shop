package suite

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	suite "github.com/FelishaK/logStorage/tests"
)

func TestSaveLogs(t *testing.T) {
	_, st := suite.New(t)

	var body []map[string]any

	d1 := map[string]any{
     "unix_time": 1657861095,
     "level": "INFO", 
     "pathname": "C:\\proj\\ecommerce\\infrastructure\\postgres\\app.py", 
     "message": "Successful db connection via: postgresql+asyncpg://postgres:postgres@localhost:5433/proj_db",
	}
	
	body = append(body, d1)

	jsonBody, err := json.Marshal(body)
	if err != nil {
		panic(err)
	}
	buf := bytes.NewBuffer(jsonBody)
	req := httptest.NewRequest(http.MethodPost, "/save", buf)
	req.Header.Set("Content-Type", "application/json")

	//response writer
	rw := httptest.NewRecorder()
	//call handler
	st.LogServ.SaveLogs(rw, req)

	if rw.Code != 201 {
		t.Errorf("got HTTP status code %d, expected 201", rw.Code)
	}
	
}