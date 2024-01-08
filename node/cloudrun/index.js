var express = require("express");
const app = express();

app.use('/', (req, res) => {
  res.status(200).send('ok');
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`Server is running on port: ${PORT}`);
})
