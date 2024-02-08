# Appsync

Go Lambda -> Appsync -> Python Lambda

You'll need to manually set up an Appsync endpoint in the UI and give it the
Python Lambda as the dataset.  Deploy the lambdas first so it's findable.

Define the schema as

```
schema {
	query: Query
}
type Query {
	hello(id: ID!): String
}
```

Then add the resolver for the `hello` field.
