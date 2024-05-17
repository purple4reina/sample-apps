use lambda_http::{Adapter, Body, Error, lambda_runtime, Request, Response};
use lambda_http::http::StatusCode;
use lambda_http::tower::{ServiceBuilder, ServiceExt};
use lambda_http::tracing::instrument;
use lambda_http::tracing::subscriber::{EnvFilter, Registry};
use lambda_http::tracing::subscriber::layer::SubscriberExt;
use opentelemetry::KeyValue;
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::{Resource, trace};
use opentelemetry_sdk::trace::Sampler;
use opentelemetry_semantic_conventions::resource;
use serde::Deserialize;
use tracing::{info, info_span};
use url::Url;

pub fn setup_tracer(conf: &Config) -> trace::TracerProvider {
    let tracer = opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(
            opentelemetry_otlp::new_exporter()
                .tonic()
                .with_endpoint(Url::parse(&conf.url.to_string()).unwrap()),
        )
        .with_trace_config(trace::config()
            .with_sampler(Sampler::TraceIdRatioBased(conf.sampling_ratio))
            .with_resource(Resource::new(vec![
                KeyValue::new(resource::SERVICE_NAME, conf.service_name.to_string()),
            ])))
        .install_batch(opentelemetry_sdk::runtime::Tokio)
        .expect("failed to install opentelemetry tracer");
    let tracer_provider = tracer
        .provider()
        .expect("failed to get tracer provider, this should never happen because we just installed the tracer");

    let telemetry_layer = tracing_opentelemetry::layer().with_tracer(tracer);
    let subscriber = Registry::default()
        .with(telemetry_layer)
        .with(EnvFilter::new("info".to_string()));
    tracing::subscriber::set_global_default(subscriber)
        .expect("failed to set global default tracing subscriber");
    tracer_provider
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let conf = envy::from_env::<Config>()?;
    let tracer_provider = setup_tracer(&conf);

    let service_fn = ServiceBuilder::new()
        .layer_fn(Adapter::from)
        .service_fn(|event: Request| f(event));
    lambda_runtime::run(service_fn.then(|res| async {
        for res in tracer_provider.force_flush() {
            if let Err(e) = res {
                info!("force flush error: {:?}", e);
            }
        }
        res
    }))
        .await
}

#[derive(Debug, Deserialize)]
pub struct Config {
    service_name: String,
    url: String,
    sampling_ratio: f64,
}

#[instrument]
pub async fn f(_: Request) -> Result<Response<Body>, Error> {
    for i in 0..5 {
        let i = i;
        info_span!("outer", i = i)
            .in_scope(|| async move {
                for j in 0..5 {
                    info_span!("inner", i = i, j = j)
                        .in_scope(|| async move {
                            println!("in span, {}-{}", i, j);
                        })
                        .await
                }
            })
            .await
    }

    Ok(Response::builder()
        .status(StatusCode::OK)
        .body(Body::Empty)
        .unwrap())
}
