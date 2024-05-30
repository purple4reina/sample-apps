# PGO

Add the following to the extension code and push to sandbox.

```golang
const pprofFile = "/tmp/cpu.prof"

func startProfiling() {
	f, err := os.Create(pprofFile)
	if err != nil {
		panic(err)
	}
	defer f.Close()
	for {
		if err := pprof.StartCPUProfile(f); err != nil {
			panic(err)
		}
		time.Sleep(10 * time.Minute)
		pprof.StopCPUProfile()
	}
}

func main() {
	go startProfiling()

	// run the agent
	err := fxutil.OneShot(runAgent)

	if err != nil {
		log.Error(err)
		os.Exit(-1)
	}
}
```
