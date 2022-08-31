module.exports.datetime = function() {
  var today = new Date();
  var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var dateTime = date+'T'+time;
  console.log("⏰ deploying serverless function at:", dateTime);
  return 'deploy_time:'+dateTime;
}();
