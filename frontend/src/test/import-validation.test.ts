/**
 * Import Validation Tests
 * Comprehensive testing to catch missing imports, CSS files, and dependency issues
 */
import { describe, expect, it } from 'vitest';
import { readdir, readFile, stat } from 'fs/promises';
import { join, extname, dirname, resolve } from 'path';
import { existsSync } from 'fs';

// Component and file patterns to validate
const IMPORT_PATTERNS = {
  CSS: /import\s+['"]([^'"]+\.css)['"]/g,
  JS_TS: /import.*from\s+['"]([^'"]+)['"]/g,
  RELATIVE: /import.*from\s+['"](\.[^'"]+)['"]/g,
  ABSOLUTE: /import.*from\s+['"](@[^'"]+)['"]/g,
} as const;

const SRC_DIR = resolve(__dirname, '../');
const COMPONENTS_DIR = resolve(SRC_DIR, 'components');
const UI_DIR = resolve(COMPONENTS_DIR, 'ui');

/**
 * Recursively find all TypeScript/JavaScript files
 */
async function findSourceFiles(dir: string, extensions = ['.ts', '.tsx', '.js', '.jsx']): Promise<string[]> {
  const files: string[] = [];
  
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      
      if (entry.isDirectory() && entry.name !== 'node_modules' && !entry.name.startsWith('.')) {
        const subFiles = await findSourceFiles(fullPath, extensions);
        files.push(...subFiles);
      } else if (entry.isFile() && extensions.includes(extname(entry.name))) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    console.warn(`Warning: Could not read directory ${dir}:`, error);
  }
  
  return files;
}

/**
 * Extract imports from file content
 */
function extractImports(content: string, pattern: RegExp): string[] {
  const imports: string[] = [];
  let match;
  
  while ((match = pattern.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  return imports;
}

/**
 * Resolve import path relative to file
 */
function resolveImportPath(importPath: string, fromFile: string): string {
  const fileDir = dirname(fromFile);
  
  // Handle relative imports
  if (importPath.startsWith('.')) {
    return resolve(fileDir, importPath);
  }
  
  // Handle absolute imports with @
  if (importPath.startsWith('@')) {
    return resolve(SRC_DIR, importPath.substring(2));
  }
  
  // Return as-is for node_modules imports
  return importPath;
}

/**
 * Check if import target exists (with common extensions)
 */
function importExists(importPath: string, fromFile: string): boolean {
  const resolvedPath = resolveImportPath(importPath, fromFile);
  
  // Skip node_modules imports
  if (!importPath.startsWith('.') && !importPath.startsWith('@')) {
    return true;
  }
  
  // Check exact path
  if (existsSync(resolvedPath)) return true;
  
  // Check with common extensions
  const extensions = ['.ts', '.tsx', '.js', '.jsx', '.css', '.scss'];
  for (const ext of extensions) {
    if (existsSync(resolvedPath + ext)) return true;
  }
  
  // Check for index files
  const indexExtensions = ['/index.ts', '/index.tsx', '/index.js', '/index.jsx'];
  for (const indexExt of indexExtensions) {
    if (existsSync(resolvedPath + indexExt)) return true;
  }
  
  return false;
}

describe('Import Validation', () => {
  describe('CSS Import Validation', () => {
    it('should validate all CSS imports exist', async () => {
      const sourceFiles = await findSourceFiles(SRC_DIR);
      const missingCssFiles: Array<{ file: string; import: string }> = [];
      
      for (const file of sourceFiles) {
        try {
          const content = await readFile(file, 'utf-8');
          const cssImports = extractImports(content, IMPORT_PATTERNS.CSS);
          
          for (const cssImport of cssImports) {
            if (!importExists(cssImport, file)) {
              missingCssFiles.push({ file, import: cssImport });
            }
          }
        } catch (error) {
          console.warn(`Warning: Could not read file ${file}:`, error);
        }
      }
      
      if (missingCssFiles.length > 0) {
        const errorMessage = missingCssFiles
          .map(({ file, import: imp }) => `${file}: ${imp}`)
          .join('\n');
        
        expect.fail(`Missing CSS files:\n${errorMessage}`);
      }
      
      expect(missingCssFiles).toHaveLength(0);
    });

    it('should specifically validate LoadingSpinner CSS exists', () => {
      const cssPath = resolve(UI_DIR, 'LoadingSpinner.css');
      expect(existsSync(cssPath)).toBe(true);
    });
  });

  describe('Component Import Validation', () => {
    it('should validate all relative imports exist', async () => {
      const sourceFiles = await findSourceFiles(COMPONENTS_DIR);
      const missingImports: Array<{ file: string; import: string }> = [];
      
      for (const file of sourceFiles) {
        try {
          const content = await readFile(file, 'utf-8');
          const relativeImports = extractImports(content, IMPORT_PATTERNS.RELATIVE);
          
          for (const relativeImport of relativeImports) {
            if (!importExists(relativeImport, file)) {
              missingImports.push({ file, import: relativeImport });
            }
          }
        } catch (error) {
          console.warn(`Warning: Could not read file ${file}:`, error);
        }
      }
      
      if (missingImports.length > 0) {
        const errorMessage = missingImports
          .map(({ file, import: imp }) => `${file}: ${imp}`)
          .join('\n');
        
        expect.fail(`Missing relative imports:\n${errorMessage}`);
      }
      
      expect(missingImports).toHaveLength(0);
    });

    it('should validate all absolute (@) imports exist', async () => {
      const sourceFiles = await findSourceFiles(SRC_DIR);
      const missingImports: Array<{ file: string; import: string }> = [];
      
      for (const file of sourceFiles) {
        try {
          const content = await readFile(file, 'utf-8');
          const absoluteImports = extractImports(content, IMPORT_PATTERNS.ABSOLUTE);
          
          for (const absoluteImport of absoluteImports) {
            if (!importExists(absoluteImport, file)) {
              missingImports.push({ file, import: absoluteImport });
            }
          }
        } catch (error) {
          console.warn(`Warning: Could not read file ${file}:`, error);
        }
      }
      
      if (missingImports.length > 0) {
        const errorMessage = missingImports
          .map(({ file, import: imp }) => `${file}: ${imp}`)
          .join('\n');
        
        expect.fail(`Missing absolute imports:\n${errorMessage}`);
      }
      
      expect(missingImports).toHaveLength(0);
    });
  });

  describe('UI Component Import Integrity', () => {
    it('should validate all UI components have proper imports', async () => {
      const uiFiles = await findSourceFiles(UI_DIR, ['.tsx', '.ts']);
      const issues: string[] = [];
      
      for (const file of uiFiles) {
        try {
          const content = await readFile(file, 'utf-8');
          const filename = file.split('/').pop() || '';
          
          // Check for React import in .tsx files
          if (filename.endsWith('.tsx') && !content.includes('React')) {
            // Allow for newer React 18+ JSX transform (no explicit React import needed)
            const hasJSX = /<[A-Z]/.test(content) || /<[a-z]+[A-Z]/.test(content);
            if (hasJSX && !content.includes('React')) {
              // This is actually OK in React 18+ with new JSX transform
            }
          }
          
          // Check for CSS imports that should exist
          const cssImports = extractImports(content, IMPORT_PATTERNS.CSS);
          for (const cssImport of cssImports) {
            if (!importExists(cssImport, file)) {
              issues.push(`${filename}: Missing CSS file ${cssImport}`);
            }
          }
          
        } catch (error) {
          issues.push(`${file}: Could not read file - ${error}`);
        }
      }
      
      if (issues.length > 0) {
        expect.fail(`UI Component issues:\n${issues.join('\n')}`);
      }
      
      expect(issues).toHaveLength(0);
    });
  });

  describe('Build-Critical Import Validation', () => {
    it('should validate critical component imports that could break builds', async () => {
      const criticalFiles = [
        resolve(UI_DIR, 'LoadingSpinner.tsx'),
        resolve(COMPONENTS_DIR, 'common/ErrorDisplay.tsx'),
        resolve(SRC_DIR, 'main.tsx'),
      ];
      
      const issues: string[] = [];
      
      for (const file of criticalFiles) {
        if (!existsSync(file)) {
          continue; // Skip if file doesn't exist
        }
        
        try {
          const content = await readFile(file, 'utf-8');
          const allImports = extractImports(content, IMPORT_PATTERNS.JS_TS);
          
          for (const importPath of allImports) {
            // Skip node_modules
            if (!importPath.startsWith('.') && !importPath.startsWith('@')) {
              continue;
            }
            
            if (!importExists(importPath, file)) {
              issues.push(`${file}: Missing import ${importPath}`);
            }
          }
        } catch (error) {
          issues.push(`${file}: Could not validate - ${error}`);
        }
      }
      
      if (issues.length > 0) {
        expect.fail(`Critical import issues that could break builds:\n${issues.join('\n')}`);
      }
      
      expect(issues).toHaveLength(0);
    });
  });
});

describe('Vite Build Compatibility', () => {
  it('should ensure all imports are compatible with Vite resolver', async () => {
    const sourceFiles = await findSourceFiles(SRC_DIR);
    const incompatibleImports: Array<{ file: string; import: string; reason: string }> = [];
    
    for (const file of sourceFiles) {
      try {
        const content = await readFile(file, 'utf-8');
        const allImports = extractImports(content, IMPORT_PATTERNS.JS_TS);
        
        for (const importPath of allImports) {          
          // Check for problematic import patterns
          if (importPath.includes('\\\\')) {
            incompatibleImports.push({
              file,
              import: importPath,
              reason: 'Contains double backslashes'
            });
          }
          
          if (importPath.endsWith('/')) {
            incompatibleImports.push({
              file,
              import: importPath,
              reason: 'Ends with slash (should specify file or use index)'
            });
          }
          
          // Check for Windows-style paths in imports
          if (importPath.includes('\\\\') && !importPath.startsWith('node_modules')) {
            incompatibleImports.push({
              file,
              import: importPath,
              reason: 'Uses Windows-style paths'
            });
          }
        }
      } catch (error) {
        console.warn(`Warning: Could not read file ${file}:`, error);
      }
    }
    
    if (incompatibleImports.length > 0) {
      const errorMessage = incompatibleImports
        .map(({ file, import: imp, reason }) => `${file}: ${imp} (${reason})`)
        .join('\n');
      
      expect.fail(`Vite-incompatible imports:\n${errorMessage}`);
    }
    
    expect(incompatibleImports).toHaveLength(0);
  });
});