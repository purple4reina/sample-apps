require 'redis-classy'
require 'redis-mutex'

RedisClassy.redis = Redis.new

puts "I'm unlocked!"

RedisMutex.with_lock(:helloworld, block: 0, expire: 15) do
  puts "I'm locked!"
  10.times do
    sleep(1)
    print "."
  end
  puts
  puts "About to unlock!"
end

puts "I'm unlocked!"
