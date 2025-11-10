package com.example.key_request_producer.controller;

import com.example.key_request_producer.model.GeneratedKey;
import com.example.key_request_producer.service.KeyService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/keys")
public class KeyController {

    private final KeyService keyService;

    public KeyController(KeyService keyService) {
        this.keyService = keyService;
    }

    @PostMapping("/request")
    public ResponseEntity<String> requestKey() {
        String requestId = keyService.requestKey();
        return ResponseEntity.ok(requestId);
    }

    @GetMapping("/generated")
    public ResponseEntity<List<GeneratedKey>> getGeneratedKeys() {
        return ResponseEntity.ok(keyService.getReceivedKeys());
    }

    @DeleteMapping("/clear")
    public ResponseEntity<Void> clearKeys() {
        keyService.clearReceivedKeys();
        return ResponseEntity.ok().build();
    }
}
