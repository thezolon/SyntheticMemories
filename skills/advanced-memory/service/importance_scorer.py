"""Automatic importance scoring for memories."""

import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ImportanceScorer:
    """Score memory importance based on content analysis."""
    
    # Keywords that indicate high importance
    HIGH_IMPORTANCE_KEYWORDS = {
        'prefer', 'always', 'never', 'important', 'critical', 'remember',
        'favorite', 'hate', 'love', 'must', 'need', 'want', 'goal',
        'project', 'working on', 'building', 'password', 'api key',
        'credential', 'secret', 'decision', 'learned', 'mistake'
    }
    
    # Keywords that indicate low importance
    LOW_IMPORTANCE_KEYWORDS = {
        'maybe', 'might', 'perhaps', 'just', 'okay', 'ok', 'thanks',
        'got it', 'sure', 'cool', 'nice', 'yeah', 'yep', 'hmm'
    }
    
    def __init__(self):
        logger.info("Initialized ImportanceScorer")
    
    def score(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """
        Score content importance from 0-10.
        
        Args:
            content: Text to score
            metadata: Optional metadata (source, context, etc.)
            
        Returns:
            Importance score (0-10)
        """
        score = 5  # Default neutral score
        content_lower = content.lower()
        
        # Length heuristic (very short = likely low importance)
        if len(content) < 10:
            score -= 2
        elif len(content) > 100:
            score += 1
        
        # High importance keywords
        high_matches = sum(1 for kw in self.HIGH_IMPORTANCE_KEYWORDS if kw in content_lower)
        score += min(high_matches, 3)  # Cap at +3
        
        # Low importance keywords
        low_matches = sum(1 for kw in self.LOW_IMPORTANCE_KEYWORDS if kw in content_lower)
        score -= min(low_matches, 3)  # Cap at -3
        
        # Question marks often indicate temporary context
        if content.count('?') > 0:
            score -= 1
        
        # Contains URLs (often important references)
        if re.search(r'https?://', content):
            score += 1
        
        # Contains code blocks (technical decisions)
        if '```' in content or '`' in content:
            score += 1
        
        # Contains dates (temporal anchoring)
        if re.search(r'\d{4}-\d{2}-\d{2}', content):
            score += 1
        
        # Metadata boosters
        if metadata:
            # Explicit user preference
            if metadata.get('type') == 'preference':
                score += 2
            
            # Security-related
            if metadata.get('security'):
                score += 3
            
            # Project-related
            if metadata.get('project'):
                score += 1
        
        # Clamp to 0-10 range
        score = max(0, min(10, score))
        
        logger.debug(f"Scored content (len={len(content)}): {score}/10")
        return score
    
    def should_store(self, score: int, threshold: int = 5) -> bool:
        """
        Determine if a memory should be stored based on importance.
        
        Args:
            score: Importance score
            threshold: Minimum score to store
            
        Returns:
            True if should store, False otherwise
        """
        return score >= threshold
    
    def should_curate(self, score: int, threshold: int = 7) -> bool:
        """
        Determine if a memory should be curated to MEMORY.md.
        
        Args:
            score: Importance score
            threshold: Minimum score for curation
            
        Returns:
            True if should curate, False otherwise
        """
        return score >= threshold
