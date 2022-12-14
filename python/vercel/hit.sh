#!/bin/bash

keys="
    $DD_PERSONAL_API_KEY
    $DD_PERSONAL_TWO_API_KEY
"
urls="
    https://ata73hbeyem5iun3bbjsdg364m0dshkp.lambda-url.sa-east-1.on.aws
"
#    https://uh6ghrre7kdrctvbbz75eb24nm0ppbzf.lambda-url.sa-east-1.on.aws
#    https://vkf7w2xarfu56yf5rcthdauzt40acobw.lambda-url.sa-east-1.on.aws
#    https://546bvtv2dawngj5dyeabxbk6le0hizfm.lambda-url.sa-east-1.on.aws
#    https://xqbr2re6uml2ahubczz4hra73y0berzu.lambda-url.sa-east-1.on.aws

while true
do
    for api_key in $keys
    do
        for url in $urls
        do
            echo
            echo "api_key: $api_key"
            echo "url:     $url"
            curl $url/$api_key/datadoghq.com &
        done
    done

    sleep 0.1
done
