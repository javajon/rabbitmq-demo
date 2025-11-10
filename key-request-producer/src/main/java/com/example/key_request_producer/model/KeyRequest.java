package com.example.key_request_producer.model;

import java.time.LocalDateTime;

public class KeyRequest {
    private String requestId;
    private LocalDateTime timestamp;

    public KeyRequest() {
        this.timestamp = LocalDateTime.now();
    }

    public KeyRequest(String requestId) {
        this.requestId = requestId;
        this.timestamp = LocalDateTime.now();
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}
