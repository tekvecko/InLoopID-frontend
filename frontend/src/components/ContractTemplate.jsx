import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: { padding: 40, fontFamily: 'Helvetica' },
  header: { fontSize: 24, marginBottom: 20, textAlign: 'center', color: '#1e293b' },
  section: { margin: 10, padding: 10 },
  text: { fontSize: 12, lineHeight: 1.5, color: '#334155' },
  signatureBlock: { marginTop: 50, borderTop: '1px solid #94a3b8', paddingTop: 10, width: '40%' }
});

export const ContractTemplate = ({ employeeName, role, salary }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <Text style={styles.header}>Employment Contract</Text>
      <View style={styles.section}>
        <Text style={styles.text}>
          This is an auto-generated agreement between InLoopID Protocol and {employeeName}.
        </Text>
        <Text style={styles.text}>Role: {role}</Text>
        <Text style={styles.text}>Compensation: {salary}</Text>
      </View>
      <View style={styles.signatureBlock}>
        <Text style={{ fontSize: 10, color: '#64748b' }}>Digital Signature (Client-Side Hash)</Text>
      </View>
    </Page>
  </Document>
);
