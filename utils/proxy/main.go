package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"os"
	"time"

	"github.com/elazarl/goproxy"
)

const (
	extensionNameHeader      = "Lambda-Extension-Name"
	extensionIdentiferHeader = "Lambda-Extension-Identifier"
	filename                 = "proxy-extension"
)

var (
	lambdaURL = fmt.Sprintf("http://%s/2020-01-01/extension", os.Getenv("AWS_LAMBDA_RUNTIME_API"))
)

func listener(port string) net.Listener {
	l, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatal(err)
	}
	return l
}

type roundTripper func(*http.Request) (*http.Response, error)

func (r roundTripper) RoundTrip(req *http.Request) (*http.Response, error) {
	return r(req)
}

func newProxy() http.Handler {
	proxy := goproxy.NewProxyHttpServer()
	proxy.Verbose = true
	proxy.OnRequest().DoFunc(
		func(req *http.Request, ctx *goproxy.ProxyCtx) (*http.Request, *http.Response) {
			if req.Body != nil {
				if body, err := ioutil.ReadAll(req.Body); err == nil {
					log.Printf("[PROXY] path: %s, method: %s, body: %s\n",
						req.URL.Path, req.Method, string(body))
					req.Body = ioutil.NopCloser(bytes.NewBuffer(body))
				} else {
					log.Printf("[PROXY] error reading request body: %s\n", err)
				}
				req.Body.Close()
			} else {
				log.Printf("[PROXY] received request without a body\n")
			}
			return req, nil
		})
	return proxy
}

func registerExtension() {
	req, err := http.NewRequest("POST", lambdaURL+"/register", bytes.NewBuffer([]byte(`{"events":[]}`)))
	if err != nil {
		log.Printf("[PROXY] error creating register request: %s\n", err)
	}
	req.Header.Set(extensionNameHeader, filename)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Printf("[PROXY] error doing register request: %s\n", err)
	}
	resp.Body.Close()
	extensionID := resp.Header.Get(extensionIdentiferHeader)
	log.Printf("[PROXY] using extension id %s\n", extensionID)
	for {
		req, err = http.NewRequest("GET", lambdaURL+"/event/next", nil)
		if err != nil {
			log.Printf("[PROXY] error creating next request: %s\n", err)
		}
		req.Header.Set(extensionIdentiferHeader, extensionID)
		resp, err = http.DefaultClient.Do(req)
		if err != nil {
			log.Printf("[PROXY] error doing next request: %s\n", err)
		}
		resp.Body.Close()
		time.Sleep(100 * time.Millisecond)
	}
}

func main() {
	proxy := newProxy()

	l := listener(":3333")
	defer l.Close()

	go http.Serve(l, proxy)

	registerExtension()
}
