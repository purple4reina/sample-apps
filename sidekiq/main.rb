require 'sidekiq'
require 'sidekiq-status'

Sidekiq.configure_client do |config|
  Sidekiq::Status.configure_client_middleware config, expiration: 300
end
Sidekiq.configure_server do |config|
  Sidekiq::Status.configure_server_middleware config, expiration: 300
  Sidekiq::Status.configure_client_middleware config, expiration: 300
  config.options[:timeout] = 0.01
end

class ExampleJob
  include Sidekiq::Worker
  include Sidekiq::Status::Worker

  sidekiq_options retry: 0

  def perform(howlong=5)
    puts "--------------------WORKER STARTING---------------------"
    sleep howlong
    store(slept: howlong)
    puts "--------------------WORKER DONE---------------------"
  end
end

if __FILE__ == $0
  job_id = ExampleJob.perform_async(10)

  15.times do
    status = Sidekiq::Status::status(job_id)
    puts "job_id: #{job_id}, status: #{status.inspect}"
    sleep 1
  end
end
