#!/bin/bash
# Setup script for persistent trading bot

echo "🚀 Setting up persistent trading bot..."
echo "======================================"

# Stop current bot if running
echo "🛑 Stopping current bot..."
pkill -f working_ibkr_bot.py

# Wait a moment
sleep 2

# Copy launch agent to system location
echo "📁 Installing launch agent..."
sudo cp com.user.tradingbot.plist ~/Library/LaunchAgents/

# Set correct permissions
echo "🔐 Setting permissions..."
chmod 644 ~/Library/LaunchAgents/com.user.tradingbot.plist

# Load the launch agent
echo "⚡ Loading launch agent..."
launchctl load ~/Library/LaunchAgents/com.user.tradingbot.plist

# Start the bot
echo "🚀 Starting persistent bot..."
launchctl start com.user.tradingbot

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Your bot will now:"
echo "   ✅ Start automatically when you log in"
echo "   ✅ Restart automatically when laptop wakes from sleep"
echo "   ✅ Keep running in background"
echo "   ✅ Survive system sleep/wake cycles"
echo ""
echo "📋 Useful commands:"
echo "   Check status: launchctl list | grep tradingbot"
echo "   Stop bot: launchctl stop com.user.tradingbot"
echo "   Start bot: launchctl start com.user.tradingbot"
echo "   View logs: tail -20 trading_bot_launch.log"
echo ""
echo "🔋 To prevent sleep while trading:"
echo "   caffeinate -i  # Prevents sleep indefinitely"
echo "   caffeinate -t 3600  # Prevents sleep for 1 hour"
