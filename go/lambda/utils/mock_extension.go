package utils

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func StartMockExtension() {
	fmt.Println("starting fake extension")
	http.HandleFunc("/v0.4/traces", func(w http.ResponseWriter, req *http.Request) {
		fmt.Println("--------------------TRACE RECEIVED---------------------")
		body, _ := ioutil.ReadAll(req.Body)
		fmt.Printf("string(body): %#v\n", string(body))
		w.WriteHeader(500)
	})
	http.ListenAndServe(":1234", nil)
}
