package com.example.bank.service;
import org.springframework.jdbc.core.JdbcTemplate;
 
import org.springframework.stereotype.Service;
@Service
 
public class TransferService {
 
    private final JdbcTemplate jdbc;
    public TransferService(JdbcTemplate jdbc) {
 
        this.jdbc = jdbc;
 
    }

 
    public void transfer(long fromId, long toId, int amount) {
 
        jdbc.update("UPDATE account SET balance = balance - ? WHERE id = ?", amount, fromId);
        if (amount > 5000) {
 
            throw new RuntimeException("Simulated failure after debit");
 
        }
        jdbc.update("UPDATE account SET balance = balance + ? WHERE id = ?", amount, toId);
 
    }
 
}
