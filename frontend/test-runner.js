#!/usr/bin/env node

/**
 * Comprehensive test runner for Office and Business Plan functionality
 * Runs all test suites and generates coverage reports
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function runCommand(command, description) {
  log(`\n🔄 ${description}...`, 'cyan');
  try {
    const output = execSync(command, { encoding: 'utf8', stdio: 'inherit' });
    log(`✅ ${description} completed successfully`, 'green');
    return true;
  } catch (error) {
    log(`❌ ${description} failed`, 'red');
    log(`Error: ${error.message}`, 'red');
    return false;
  }
}

function checkFileExists(filePath, description) {
  if (fs.existsSync(filePath)) {
    log(`✅ ${description} exists`, 'green');
    return true;
  } else {
    log(`❌ ${description} not found`, 'red');
    return false;
  }
}

function generateReport() {
  log('\n📊 Generating Test Report...', 'magenta');
  
  const report = {
    timestamp: new Date().toISOString(),
    environment: {
      node: process.version,
      npm: execSync('npm --version', { encoding: 'utf8' }).trim(),
      platform: process.platform,
    },
    testSuites: {
      unit: {
        description: 'Unit tests for stores and components',
        files: [
          'src/stores/__tests__/officeStore.test.ts',
          'src/stores/__tests__/businessPlanStore.test.ts',
          'src/pages/__tests__/OfficeManagement.test.tsx',
          'src/pages/__tests__/AllOffices.test.tsx',
          'src/components/business-plans/__tests__/BusinessPlanTable.test.tsx',
        ],
      },
      integration: {
        description: 'Integration tests for API endpoints',
        files: [
          'src/test/integration/office-api.test.ts',
        ],
      },
      e2e: {
        description: 'End-to-end tests for user workflows',
        files: [
          'e2e/office-management.spec.ts',
          'e2e/business-plan-workflow.spec.ts',
        ],
      },
    },
    coverage: {
      enabled: true,
      thresholds: {
        global: { branches: 80, functions: 80, lines: 80, statements: 80 },
        stores: { branches: 90, functions: 90, lines: 90, statements: 90 },
        pages: { branches: 75, functions: 75, lines: 75, statements: 75 },
        components: { branches: 70, functions: 70, lines: 70, statements: 70 },
      },
    },
  };

  // Write report to file
  const reportPath = path.join(__dirname, 'test-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  log(`📄 Test report saved to: ${reportPath}`, 'blue');

  return report;
}

async function main() {
  log('🧪 Office & Business Plan Test Suite Runner', 'bright');
  log('=========================================', 'bright');

  const startTime = Date.now();
  let testResults = {
    unit: false,
    integration: false,
    e2e: false,
    coverage: false,
  };

  // Check if we're in the correct directory
  if (!fs.existsSync('package.json')) {
    log('❌ Not in a frontend project directory. Please run from frontend folder.', 'red');
    process.exit(1);
  }

  // Check test dependencies
  log('\n🔍 Checking test dependencies...', 'yellow');
  const dependencies = [
    'vitest',
    '@playwright/test',
    '@testing-library/react',
    '@testing-library/jest-dom',
    '@testing-library/user-event',
  ];

  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  let missingDeps = [];
  dependencies.forEach(dep => {
    if (allDeps[dep]) {
      log(`✅ ${dep} (${allDeps[dep]})`, 'green');
    } else {
      log(`❌ ${dep} missing`, 'red');
      missingDeps.push(dep);
    }
  });

  if (missingDeps.length > 0) {
    log(`\n⚠️  Missing dependencies: ${missingDeps.join(', ')}`, 'yellow');
    log('Installing missing dependencies...', 'yellow');
    runCommand('npm install', 'Installing dependencies');
  }

  // Check test files exist
  log('\n📁 Checking test files...', 'yellow');
  const testFiles = [
    'src/stores/__tests__/officeStore.test.ts',
    'src/stores/__tests__/businessPlanStore.test.ts',
    'src/pages/__tests__/OfficeManagement.test.tsx',
    'src/pages/__tests__/AllOffices.test.tsx',
    'src/components/business-plans/__tests__/BusinessPlanTable.test.tsx',
    'src/test/integration/office-api.test.ts',
    'e2e/office-management.spec.ts',
    'e2e/business-plan-workflow.spec.ts',
  ];

  let missingFiles = [];
  testFiles.forEach(file => {
    if (checkFileExists(file, file)) {
      // File exists
    } else {
      missingFiles.push(file);
    }
  });

  if (missingFiles.length > 0) {
    log(`\n⚠️  Some test files are missing. This is expected if running partial test suite.`, 'yellow');
  }

  // Run Unit Tests
  log('\n🧪 Running Unit Tests...', 'bright');
  testResults.unit = runCommand('npm run test:run', 'Unit tests');

  // Run Unit Tests with Coverage
  log('\n📊 Running Unit Tests with Coverage...', 'bright');
  testResults.coverage = runCommand('npm run test:coverage', 'Coverage analysis');

  // Run Integration Tests (if backend is available)
  log('\n🔗 Running Integration Tests...', 'bright');
  try {
    // Check if backend is running
    execSync('curl -s http://localhost:8000/health || exit 1', { stdio: 'ignore' });
    log('✅ Backend is running, proceeding with integration tests', 'green');
    testResults.integration = runCommand('npm run test:run src/test/integration/', 'Integration tests');
  } catch (error) {
    log('⚠️  Backend not running, skipping integration tests', 'yellow');
    log('To run integration tests, start the backend server first', 'yellow');
    testResults.integration = 'skipped';
  }

  // Run E2E Tests (if frontend is available)
  log('\n🎭 Running End-to-End Tests...', 'bright');
  try {
    // Check if playwright is installed
    execSync('npx playwright --version', { stdio: 'ignore' });
    
    // Install browsers if needed
    log('Installing Playwright browsers...', 'yellow');
    execSync('npx playwright install', { stdio: 'inherit' });
    
    testResults.e2e = runCommand('npm run test:e2e', 'End-to-end tests');
  } catch (error) {
    log('⚠️  Playwright not properly installed, skipping E2E tests', 'yellow');
    log('Run "npx playwright install" to set up E2E testing', 'yellow');
    testResults.e2e = 'skipped';
  }

  // Generate test report
  const report = generateReport();

  // Summary
  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  log('\n📋 Test Results Summary', 'bright');
  log('======================', 'bright');
  log(`Unit Tests: ${testResults.unit ? '✅ PASSED' : '❌ FAILED'}`, testResults.unit ? 'green' : 'red');
  log(`Integration Tests: ${testResults.integration === true ? '✅ PASSED' : testResults.integration === 'skipped' ? '⏭️  SKIPPED' : '❌ FAILED'}`, testResults.integration === true ? 'green' : testResults.integration === 'skipped' ? 'yellow' : 'red');
  log(`E2E Tests: ${testResults.e2e === true ? '✅ PASSED' : testResults.e2e === 'skipped' ? '⏭️  SKIPPED' : '❌ FAILED'}`, testResults.e2e === true ? 'green' : testResults.e2e === 'skipped' ? 'yellow' : 'red');
  log(`Coverage: ${testResults.coverage ? '✅ GENERATED' : '❌ FAILED'}`, testResults.coverage ? 'green' : 'red');
  log(`\n⏱️  Total execution time: ${duration}s`, 'blue');

  // Check if coverage report exists and show path
  if (fs.existsSync('coverage/index.html')) {
    log(`\n📊 Coverage report available at: ${path.resolve('coverage/index.html')}`, 'blue');
  }

  // Check if Playwright report exists
  if (fs.existsSync('playwright-report/index.html')) {
    log(`🎭 Playwright report available at: ${path.resolve('playwright-report/index.html')}`, 'blue');
  }

  // Recommendations
  log('\n💡 Recommendations:', 'bright');
  if (!testResults.unit) {
    log('• Fix unit test failures before proceeding', 'yellow');
  }
  if (testResults.integration === 'skipped') {
    log('• Start backend server to run integration tests', 'yellow');
  }
  if (testResults.e2e === 'skipped') {
    log('• Install Playwright to run E2E tests: npx playwright install', 'yellow');
  }
  if (testResults.coverage) {
    log('• Review coverage report to identify untested code', 'yellow');
  }

  // Exit with appropriate code
  const hasFailures = !testResults.unit || testResults.integration === false || testResults.e2e === false;
  if (hasFailures) {
    log('\n❌ Some tests failed. Please review and fix issues.', 'red');
    process.exit(1);
  } else {
    log('\n🎉 All tests completed successfully!', 'green');
    process.exit(0);
  }
}

// Handle interrupts gracefully
process.on('SIGINT', () => {
  log('\n\n⚠️  Test run interrupted by user', 'yellow');
  process.exit(130);
});

process.on('SIGTERM', () => {
  log('\n\n⚠️  Test run terminated', 'yellow');
  process.exit(143);
});

// Run the test suite
main().catch(error => {
  log(`\n💥 Unexpected error: ${error.message}`, 'red');
  console.error(error.stack);
  process.exit(1);
});