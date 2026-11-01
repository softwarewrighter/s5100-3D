const fs = require('fs');
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('usage: node make-open-glb.js INPUT OUTPUT');
const data = fs.readFileSync(input);
fs.writeFileSync(output, data);
console.log(`copied ${input} -> ${output}`);
