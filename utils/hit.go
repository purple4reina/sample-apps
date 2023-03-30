// simple script to hammer at a url, using a semafor to manage resources
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
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

var (
	url = os.Getenv("URL")

	client = func() *http.Client {
		c := http.DefaultClient
		c.Transport = &http.Transport{
			MaxIdleConnsPerHost: capacity,
		}
		return c
	}()
)

const capacity = 24

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
