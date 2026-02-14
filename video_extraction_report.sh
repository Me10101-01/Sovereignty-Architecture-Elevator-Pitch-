#!/bin/bash
# LEGION Video Source Extraction Report
# GitKraken Intelligence Analysis Results

echo "🎯 LEGION VIDEO SOURCE EXTRACTION RESULTS"
echo "=========================================="
echo "Target: GitKraken Video Analysis"
echo "Timestamp: $(date)"
echo ""

echo "🔍 IDENTIFIED VIDEO SOURCES:"
echo ""

# YouTube Video IDs discovered
echo "📺 YouTube Videos Found:"
echo "1. Video ID: AxNeCQQRnsM"
echo "   Full URL: https://youtu.be/AxNeCQQRnsM"
echo "   Context: Primary embedded video with overlay"
echo "   Overlay Image: https://www.gitkraken.com/wp-content/uploads/2025/10/Group-22051.png"
echo ""

echo "2. Video ID: edsCT-MIWhs" 
echo "   Full URL: https://youtu.be/edsCT-MIWhs"
echo "   Context: Secondary embedded video"
echo "   Overlay Image: https://www.gitkraken.com/wp-content/uploads/2024/05/Group-20488-2.png"
echo ""

echo "3. Video ID: sMEs6z90KxU"
echo "   Full URL: https://youtu.be/sMEs6z90KxU"
echo "   Context: Tertiary embedded video"
echo "   Overlay Image: https://www.gitkraken.com/wp-content/uploads/2024/05/Group-20469.png"
echo ""

echo "📋 YouTube Playlist Found:"
echo "   Playlist ID: PLe6EXFvnTV7-vbeNjYa1jbIRAzgAvyQ9Z"
echo "   Full URL: https://youtube.com/playlist?list=PLe6EXFvnTV7-vbeNjYa1jbIRAzgAvyQ9Z"
echo ""

echo "📢 GitKraken YouTube Channel:"
echo "   Channel URL: https://www.youtube.com/gitkraken"
echo ""

echo "🔧 VIDEO CONFIGURATION ANALYSIS:"
echo "• Video Type: YouTube embedded"
echo "• Privacy Mode: Enabled (yt_privacy=yes)"
echo "• Modest Branding: Enabled"
echo "• Lazy Loading: Enabled"
echo "• Controls: Enabled"
echo "• Image Overlay: Custom overlays for each video"
echo ""

echo "🎬 RECOMMENDED RECONNAISSANCE:"
echo "1. Analyze specific YouTube videos:"
for video_id in "AxNeCQQRnsM" "edsCT-MIWhs" "sMEs6z90KxU"; do
    echo "   curl -s \"https://www.youtube.com/watch?v=$video_id\" | grep -E \"(title|description)\""
done
echo ""

echo "2. Extract video metadata:"
for video_id in "AxNeCQQRnsM" "edsCT-MIWhs" "sMEs6z90KxU"; do
    echo "   youtube-dl --dump-json \"https://youtu.be/$video_id\" 2>/dev/null || echo 'youtube-dl not available'"
done
echo ""

echo "3. Analyze GitKraken YouTube channel:"
echo "   curl -s \"https://www.youtube.com/c/gitkraken\" | grep -E \"(subscriber|video|playlist)\""
echo ""

echo "🏆 LEGION ANALYSIS COMPLETE"
echo "Video sources successfully identified and catalogued"