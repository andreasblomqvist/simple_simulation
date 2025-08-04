#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function findAntdUsage(dir, results = []) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
      findAntdUsage(fullPath, results);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      if (content.includes('antd') || content.includes('@ant-design')) {
        const lines = content.split('\n');
        const matches = [];
        lines.forEach((line, index) => {
          if (line.includes('antd') || line.includes('@ant-design')) {
            matches.push(`  Line ${index + 1}: ${line.trim()}`);
          }
        });
        if (matches.length > 0) {
          results.push({
            file: fullPath.replace(process.cwd() + '/', ''),
            matches
          });
        }
      }
    }
  }
  
  return results;
}

const srcDir = path.join(__dirname, 'src');
const results = findAntdUsage(srcDir);

console.log('\n🔍 Ant Design Usage Report:');
console.log('=' * 50);

if (results.length === 0) {
  console.log('✅ No Ant Design imports found!');
} else {
  console.log(`❌ Found ${results.length} files with Ant Design usage:\n`);
  results.forEach(result => {
    console.log(`📄 ${result.file}`);
    result.matches.forEach(match => console.log(match));
    console.log('');
  });
}