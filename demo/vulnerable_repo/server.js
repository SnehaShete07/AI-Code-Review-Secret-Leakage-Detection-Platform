const { exec } = require('child_process')

function processInput(input) {
  const cmd = "echo " + input
  exec(cmd)
  return eval(input)
}

module.exports = { processInput }
