package main

import (
	"fmt"
)

func main() {
	doIt()
	fmt.Printf("done doIt %d\n", num)
}

var num int

func doIt() {
	//p := tracer.NewPropagator(nil)
	//p.Extract(nil)
	num++
}
