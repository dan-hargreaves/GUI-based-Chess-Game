# -*- coding: utf-8 -*-

import requests
import time
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging


class StockfishError(Exception):
    """Custom exception for Stockfish API errors"""
    pass


class NetworkError(StockfishError):
    """Network-related errors"""
    pass


class APIError(StockfishError):
    """API-related errors"""
    pass


@dataclass
class StockfishResponse:
    """Structured response from Stockfish API"""
    success: bool
    best_move: Optional[str] = None
    evaluation: Optional[float] = None
    mate: Optional[int] = None
    line: Optional[str] = None
    error: Optional[str] = None


class StockfishClient:
    """
    Production-ready Stockfish API client with comprehensive error handling,
    retry logic, and proper logging.
    """
    
    def __init__(
        self,
        base_url: str = "https://stockfish.online/api/s/v2.php",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        api_key: Optional[str] = None
    ):
        """
        Initialize Stockfish API client.+
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            api_key: API key if authentication is required
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'StockfishClient/1.0'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def analyze_position(
        self, 
        fen: str, 
        depth: int = 15
    ) -> StockfishResponse:
        """
        Analyze a chess position using Stockfish engine.
        
        Args:
            fen: FEN string representing the chess position
            depth: Analysis depth (1-15, default 15)
            
        Returns:
            StockfishResponse object containing analysis results
            
        Raises:
            ValueError: If parameters are invalid
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        # Validate inputs
        if not fen or not isinstance(fen, str):
            raise ValueError("FEN string must be a non-empty string")
        
        if not isinstance(depth, int) or depth < 1 or depth > 15:
            raise ValueError("Depth must be an integer between 1 and 15")
        
        # Prepare request payload
        payload = {
            'fen': fen,
            'depth': depth
        }
        
        return self._make_request_with_retry('GET', payload)
    
    def _make_request_with_retry(
        self, 
        method: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> StockfishResponse:
        """
        Make HTTP request with retry logic and comprehensive error handling.
        """
        url = self.base_url
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Attempt {attempt + 1}: {method} {url}")
                
                if method.upper() == 'GET':
                    response = self.session.get(
                        url, 
                        params=data, 
                        timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=self.timeout
                    )
                
                # Handle HTTP errors
                response.raise_for_status()
                
                # Parse and return response
                return self._parse_response(response)
                
            except requests.exceptions.Timeout as e:
                last_exception = NetworkError(f"Request timeout after {self.timeout}s")
                self.logger.warning(f"Timeout on attempt {attempt + 1}")
                
            except requests.exceptions.ConnectionError as e:
                last_exception = NetworkError(f"Connection error: {str(e)}")
                self.logger.warning(f"Connection error on attempt {attempt + 1}")
                
            except requests.exceptions.HTTPError as e:
                if response.status_code >= 500:
                    # Server errors - retry
                    last_exception = APIError(f"Server error {response.status_code}: {response.text}")
                    self.logger.warning(f"Server error on attempt {attempt + 1}: {response.status_code}")
                else:
                    # Client errors - don't retry
                    raise APIError(f"API error {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                last_exception = NetworkError(f"Request error: {str(e)}")
                self.logger.warning(f"Request error on attempt {attempt + 1}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All retries exhausted
        self.logger.error(f"All {self.max_retries + 1} attempts failed")
        raise last_exception or NetworkError("Request failed after all retries")
    
    def _parse_response(self, response: requests.Response) -> StockfishResponse:
        """
        Parse API response into structured format.
        """
        try:
            data = response.json()
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {str(e)}")
        
        # Handle API error responses
        if not data.get('success', True):
            return StockfishResponse(
                success=False,
                error=data.get('error', 'Unknown API error')
            )
        
        # Parse successful response
        return StockfishResponse(
            success=True,
            best_move=data.get('bestmove'),
            evaluation=data.get('evaluation'),
            mate=data.get('mate'),
            line=data.get('line')
        )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.close()
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()


# Example usage and testing functions
def example_usage():
    """Example usage of the StockfishClient"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Using context manager (recommended)
    with StockfishClient() as client:
        try:
            # Analyze starting position
            result = client.analyze_position(
                fen="rnbqkbnr/pppppppp/8/8/8/8/qqqqqqqq/RNBQKBNR b KQkq - 0 1",
                depth=12
            )
            
            if result.success:
                print(f"Best move: {result.best_move}")
                print(f"Evaluation: {result.evaluation}")
                if result.mate:
                    print(f"Mate in: {result.mate}")
                print(f"Principal variation: {result.line}")
            else:
                print(f"API Error: {result.error}")
                
        except (APIError, NetworkError, ValueError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    example_usage()