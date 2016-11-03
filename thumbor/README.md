# Thumbor

https://newrelic.zendesk.com/agent/tickets/217989

1. Prepare

    ```
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

1. Run

    ```bash
    for port in 10301 10302 10303 10304
    do
        newrelic-admin run-program thumbor -p $port -l info &
    done
    ```

1. Use

    ```bash
    while true
    do
        for port in 10301 10302 10303 10304
        do
            curl -s http://localhost:10301/unsafe/300x200/http://www.waterfalls.hamilton.ca/images/Waterfall_Collage_home_sm1.jpg > /dev/null
        done

        sleep 1
    done
    ```
