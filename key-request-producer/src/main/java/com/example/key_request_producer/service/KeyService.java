package com.example.key_request_producer.service;

import com.example.key_request_producer.model.GeneratedKey;
import com.example.key_request_producer.model.KeyRequest;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class KeyService {

    private final RabbitTemplate rabbitTemplate;
    private final List<GeneratedKey> receivedKeys = new CopyOnWriteArrayList<>();

    @Value("${rabbitmq.queue.requests}")
    private String requestQueueName;

    public KeyService(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public String requestKey() {
        String requestId = UUID.randomUUID().toString();
        KeyRequest request = new KeyRequest(requestId);
        rabbitTemplate.convertAndSend(requestQueueName, request);
        return requestId;
    }

    @RabbitListener(queues = "${rabbitmq.queue.responses}")
    public void receiveGeneratedKey(GeneratedKey generatedKey) {
        receivedKeys.add(generatedKey);
        System.out.println("Received generated key: " + generatedKey.getKey() +
                         " for request: " + generatedKey.getRequestId());
    }

    public List<GeneratedKey> getReceivedKeys() {
        return new ArrayList<>(receivedKeys);
    }

    public void clearReceivedKeys() {
        receivedKeys.clear();
    }
}
