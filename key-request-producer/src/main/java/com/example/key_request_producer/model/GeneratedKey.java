package com.example.key_request_producer.model;

import java.time.LocalDateTime;

public class GeneratedKey {
    private String requestId;
    private String key;
    private LocalDateTime generatedAt;

    public GeneratedKey() {
    }

    public GeneratedKey(String requestId, String key, LocalDateTime generatedAt) {
        this.requestId = requestId;
        this.key = key;
        this.generatedAt = generatedAt;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public LocalDateTime getGeneratedAt() {
        return generatedAt;
    }

    public void setGeneratedAt(LocalDateTime generatedAt) {
        this.generatedAt = generatedAt;
    }
}
