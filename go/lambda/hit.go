package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	semafor := make(chan struct{}, capacity)

	for i := 0; i < capacity; i++ {
		semafor <- struct{}{}
	}

	for {
		go func(x struct{}) {
			defer func() { semafor <- x }()
			do()
		}(<-semafor)
	}
}

var client = func() *http.Client {
	c := http.DefaultClient
	c.Transport = &http.Transport{
		MaxIdleConnsPerHost: capacity,
	}
	return c
}()

const (
	capacity = 24
	url      = "https://6oism8kqc7.execute-api.sa-east-1.amazonaws.com/dev/simple"
)

func do() {
	resp, err := client.Get(url)
	if err != nil {
		panic(err)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	fmt.Printf(string(body))
	defer resp.Body.Close()
}
