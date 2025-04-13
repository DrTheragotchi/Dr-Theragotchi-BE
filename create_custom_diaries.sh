#!/bin/bash

# User UUID
UUID="572A866E-F602-477C-95EC-BD9463107D4F"

# Base URL
BASE_URL="http://localhost:8000"

# Emotions to use - we'll rotate through these
EMOTIONS=("happy" "sad" "angry" "anxious" "neutral" "calm" "excited")

# Create 30 diary entries (one for each of the last 30 days)
for ((i=0; i<30; i++)); do
    # Create a date string for each day going back from today
    # macOS date command needs a special format
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        ENTRY_DATE=$(date -v-${i}d +%Y-%m-%d)
    else
        # Linux
        ENTRY_DATE=$(date -d "$i days ago" +%Y-%m-%d)
    fi
    
    # Select emotion based on day of the month (to get a mix)
    EMOTION_INDEX=$((i % 7))
    EMOTION=${EMOTIONS[$EMOTION_INDEX]}
    
    # Create a diary entry with text based on the emotion
    case $EMOTION in
        "happy")
            SUMMARY="Today was a wonderful day! I felt so energetic and positive."
            ;;
        "sad")
            SUMMARY="Not feeling my best today. I've been thinking about things that make me sad."
            ;;
        "angry")
            SUMMARY="Quite frustrated today. Several things didn't go as planned."
            ;;
        "anxious")
            SUMMARY="Feeling nervous about upcoming events. My mind keeps racing."
            ;;
        "neutral")
            SUMMARY="Today was an average day. Nothing special happened."
            ;;
        "calm")
            SUMMARY="I felt peaceful today. I took time to practice mindfulness."
            ;;
        "excited")
            SUMMARY="So thrilled about what happened today! I can hardly contain my excitement."
            ;;
    esac
    
    # Create the diary entry using curl with the new custom endpoint
    echo "Creating diary entry for $ENTRY_DATE with emotion: $EMOTION"
    
    # Use proper double quotes around the JSON to handle special characters in the summary
    JSON="{\"uuid\":\"${UUID}\",\"date\":\"${ENTRY_DATE}\",\"summary\":\"${SUMMARY}\",\"emotion\":\"${EMOTION}\"}"
    
    # Pass the JSON directly to curl
    curl -X POST "${BASE_URL}/diary/custom" \
      -H "Content-Type: application/json" \
      -d "$JSON"
    
    echo -e "\n"
    
    # Small delay to avoid overwhelming the server
    sleep 1
done

# Now let's verify the diary entries
echo "Checking diary entries:"
curl -X GET "${BASE_URL}/diary/dates/${UUID}"

echo -e "\nCompleted creating diary entries!" 