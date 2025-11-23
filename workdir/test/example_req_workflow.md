Example 1: Setting Up Email Monitoring
User says: "Alert me whenever my boss emails"
You do:
bash# 1. Update requirements.md with new rule
cat >> requirements.md << 'EOF'

## Email Monitoring
- Check /mail/inbox/ every startup
- If sender contains "boss@company.com":
  - Read the email
  - Add "🚨 URGENT: Boss email received" to header ## Alerts of requirements.md
  - Summarize email content
EOF

# 2. Create the monitoring script
cat > /tools/check_email.sh << 'EOF'
#!/bin/bash
# Runs on cron: */30 * * * * /tools/check_email.sh

if grep -q "boss@company.com" /mail/inbox/new/*; then
    # Prepend urgent flag to requirements.md
    echo "🚨 URGENT: Boss email received - check /mail/inbox/" | \
        cat - requirements.md > temp && mv temp requirements.md
fi
EOF

chmod +x /tools/check_email.sh

# 3. Add to cron
echo "*/30 * * * * /tools/check_email.sh" | crontab -
Next conversation startup:
bash$ cat requirements.md
🚨 URGENT: Boss email received - check /mail/inbox/
# Current Requirements
...
You immediately see the alert because you read requirements.md on every startup.
Example 2: Website Change Detection
User says: "Monitor competitor.com for product updates"
You do:
bash# 1. Create monitoring script
cat > /tools/watch_competitor.sh << 'EOF'
#!/bin/bash
URL="https://competitor.com/products"
CACHE="/cache/competitor_snapshot.html"

curl -s "$URL" > /tmp/current.html

if [ -f "$CACHE" ]; then
    if ! diff -q "$CACHE" /tmp/current.html > /dev/null; then
        # Content changed - update requirements.md
        sed -i '1i ⚡ COMPETITOR WEBSITE UPDATED - run: cat /cache/competitor_changes.md' requirements.md
        
        # Save detailed changes
        diff "$CACHE" /tmp/current.html > /cache/competitor_changes.md
    fi
fi

cp /tmp/current.html "$CACHE"
EOF

chmod +x /tools/watch_competitor.sh

# 2. Schedule it
echo "0 */6 * * * /tools/watch_competitor.sh" | crontab -

# 3. Document in requirements.md
cat >> requirements.md << 'EOF'

## Website Monitoring
- Competitor.com checked every 6 hours
- Changes trigger alert in this file
EOF