#!/bin/bash
# Production build for testing (single thread, no hot reload)

echo "🔄 Building Next.js for production..."
npm run build

echo "🚀 Starting production server (single thread)..."
npm run start